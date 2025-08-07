#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* isutil.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petsctao.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taovecgetsubvec_ TAOVECGETSUBVEC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taovecgetsubvec_ taovecgetsubvec
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taomatgetsubmat_ TAOMATGETSUBMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taomatgetsubmat_ taomatgetsubmat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoboundstep_ TAOBOUNDSTEP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoboundstep_ taoboundstep
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoboundsolution_ TAOBOUNDSOLUTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoboundsolution_ taoboundsolution
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  taovecgetsubvec_(Vec vfull,IS is,TaoSubsetType *reduced_type,PetscReal *maskvalue,Vec *vreduced, int *ierr)
{
CHKFORTRANNULLOBJECT(vfull);
CHKFORTRANNULLOBJECT(is);
PetscBool vreduced_null = !*(void**) vreduced ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vreduced);
*ierr = TaoVecGetSubVec(
	(Vec)PetscToPointer((vfull) ),
	(IS)PetscToPointer((is) ),*reduced_type,*maskvalue,vreduced);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vreduced_null && !*(void**) vreduced) * (void **) vreduced = (void *)-2;
}
PETSC_EXTERN void  taomatgetsubmat_(Mat M,IS is,Vec v1,TaoSubsetType *subset_type,Mat *Msub, int *ierr)
{
CHKFORTRANNULLOBJECT(M);
CHKFORTRANNULLOBJECT(is);
CHKFORTRANNULLOBJECT(v1);
PetscBool Msub_null = !*(void**) Msub ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(Msub);
*ierr = TaoMatGetSubMat(
	(Mat)PetscToPointer((M) ),
	(IS)PetscToPointer((is) ),
	(Vec)PetscToPointer((v1) ),*subset_type,Msub);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! Msub_null && !*(void**) Msub) * (void **) Msub = (void *)-2;
}
PETSC_EXTERN void  taoboundstep_(Vec X,Vec XL,Vec XU,IS active_lower,IS active_upper,IS active_fixed,PetscReal *scale,Vec S, int *ierr)
{
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(XL);
CHKFORTRANNULLOBJECT(XU);
CHKFORTRANNULLOBJECT(active_lower);
CHKFORTRANNULLOBJECT(active_upper);
CHKFORTRANNULLOBJECT(active_fixed);
CHKFORTRANNULLOBJECT(S);
*ierr = TaoBoundStep(
	(Vec)PetscToPointer((X) ),
	(Vec)PetscToPointer((XL) ),
	(Vec)PetscToPointer((XU) ),
	(IS)PetscToPointer((active_lower) ),
	(IS)PetscToPointer((active_upper) ),
	(IS)PetscToPointer((active_fixed) ),*scale,
	(Vec)PetscToPointer((S) ));
}
PETSC_EXTERN void  taoboundsolution_(Vec X,Vec XL,Vec XU,PetscReal *bound_tol,PetscInt *nDiff,Vec Xout, int *ierr)
{
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(XL);
CHKFORTRANNULLOBJECT(XU);
CHKFORTRANNULLINTEGER(nDiff);
CHKFORTRANNULLOBJECT(Xout);
*ierr = TaoBoundSolution(
	(Vec)PetscToPointer((X) ),
	(Vec)PetscToPointer((XL) ),
	(Vec)PetscToPointer((XU) ),*bound_tol,nDiff,
	(Vec)PetscToPointer((Xout) ));
}
#if defined(__cplusplus)
}
#endif
