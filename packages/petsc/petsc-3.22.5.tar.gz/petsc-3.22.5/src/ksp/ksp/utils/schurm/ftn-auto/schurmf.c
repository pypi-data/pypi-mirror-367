#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* schurm.c */
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

#include "petscksp.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreateschurcomplement_ MATCREATESCHURCOMPLEMENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreateschurcomplement_ matcreateschurcomplement
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matschurcomplementsetsubmatrices_ MATSCHURCOMPLEMENTSETSUBMATRICES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matschurcomplementsetsubmatrices_ matschurcomplementsetsubmatrices
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matschurcomplementgetksp_ MATSCHURCOMPLEMENTGETKSP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matschurcomplementgetksp_ matschurcomplementgetksp
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matschurcomplementsetksp_ MATSCHURCOMPLEMENTSETKSP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matschurcomplementsetksp_ matschurcomplementsetksp
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matschurcomplementupdatesubmatrices_ MATSCHURCOMPLEMENTUPDATESUBMATRICES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matschurcomplementupdatesubmatrices_ matschurcomplementupdatesubmatrices
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matschurcomplementgetsubmatrices_ MATSCHURCOMPLEMENTGETSUBMATRICES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matschurcomplementgetsubmatrices_ matschurcomplementgetsubmatrices
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matschurcomplementcomputeexplicitoperator_ MATSCHURCOMPLEMENTCOMPUTEEXPLICITOPERATOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matschurcomplementcomputeexplicitoperator_ matschurcomplementcomputeexplicitoperator
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetschurcomplement_ MATGETSCHURCOMPLEMENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetschurcomplement_ matgetschurcomplement
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matschurcomplementsetainvtype_ MATSCHURCOMPLEMENTSETAINVTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matschurcomplementsetainvtype_ matschurcomplementsetainvtype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matschurcomplementgetainvtype_ MATSCHURCOMPLEMENTGETAINVTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matschurcomplementgetainvtype_ matschurcomplementgetainvtype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreateschurcomplementpmat_ MATCREATESCHURCOMPLEMENTPMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreateschurcomplementpmat_ matcreateschurcomplementpmat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matschurcomplementgetpmat_ MATSCHURCOMPLEMENTGETPMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matschurcomplementgetpmat_ matschurcomplementgetpmat
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matcreateschurcomplement_(Mat A00,Mat Ap00,Mat A01,Mat A10,Mat A11,Mat *S, int *ierr)
{
CHKFORTRANNULLOBJECT(A00);
CHKFORTRANNULLOBJECT(Ap00);
CHKFORTRANNULLOBJECT(A01);
CHKFORTRANNULLOBJECT(A10);
CHKFORTRANNULLOBJECT(A11);
PetscBool S_null = !*(void**) S ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(S);
*ierr = MatCreateSchurComplement(
	(Mat)PetscToPointer((A00) ),
	(Mat)PetscToPointer((Ap00) ),
	(Mat)PetscToPointer((A01) ),
	(Mat)PetscToPointer((A10) ),
	(Mat)PetscToPointer((A11) ),S);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! S_null && !*(void**) S) * (void **) S = (void *)-2;
}
PETSC_EXTERN void  matschurcomplementsetsubmatrices_(Mat S,Mat A00,Mat Ap00,Mat A01,Mat A10,Mat A11, int *ierr)
{
CHKFORTRANNULLOBJECT(S);
CHKFORTRANNULLOBJECT(A00);
CHKFORTRANNULLOBJECT(Ap00);
CHKFORTRANNULLOBJECT(A01);
CHKFORTRANNULLOBJECT(A10);
CHKFORTRANNULLOBJECT(A11);
*ierr = MatSchurComplementSetSubMatrices(
	(Mat)PetscToPointer((S) ),
	(Mat)PetscToPointer((A00) ),
	(Mat)PetscToPointer((Ap00) ),
	(Mat)PetscToPointer((A01) ),
	(Mat)PetscToPointer((A10) ),
	(Mat)PetscToPointer((A11) ));
}
PETSC_EXTERN void  matschurcomplementgetksp_(Mat S,KSP *ksp, int *ierr)
{
CHKFORTRANNULLOBJECT(S);
PetscBool ksp_null = !*(void**) ksp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ksp);
*ierr = MatSchurComplementGetKSP(
	(Mat)PetscToPointer((S) ),ksp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ksp_null && !*(void**) ksp) * (void **) ksp = (void *)-2;
}
PETSC_EXTERN void  matschurcomplementsetksp_(Mat S,KSP ksp, int *ierr)
{
CHKFORTRANNULLOBJECT(S);
CHKFORTRANNULLOBJECT(ksp);
*ierr = MatSchurComplementSetKSP(
	(Mat)PetscToPointer((S) ),
	(KSP)PetscToPointer((ksp) ));
}
PETSC_EXTERN void  matschurcomplementupdatesubmatrices_(Mat S,Mat A00,Mat Ap00,Mat A01,Mat A10,Mat A11, int *ierr)
{
CHKFORTRANNULLOBJECT(S);
CHKFORTRANNULLOBJECT(A00);
CHKFORTRANNULLOBJECT(Ap00);
CHKFORTRANNULLOBJECT(A01);
CHKFORTRANNULLOBJECT(A10);
CHKFORTRANNULLOBJECT(A11);
*ierr = MatSchurComplementUpdateSubMatrices(
	(Mat)PetscToPointer((S) ),
	(Mat)PetscToPointer((A00) ),
	(Mat)PetscToPointer((Ap00) ),
	(Mat)PetscToPointer((A01) ),
	(Mat)PetscToPointer((A10) ),
	(Mat)PetscToPointer((A11) ));
}
PETSC_EXTERN void  matschurcomplementgetsubmatrices_(Mat S,Mat *A00,Mat *Ap00,Mat *A01,Mat *A10,Mat *A11, int *ierr)
{
CHKFORTRANNULLOBJECT(S);
PetscBool A00_null = !*(void**) A00 ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A00);
PetscBool Ap00_null = !*(void**) Ap00 ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(Ap00);
PetscBool A01_null = !*(void**) A01 ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A01);
PetscBool A10_null = !*(void**) A10 ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A10);
PetscBool A11_null = !*(void**) A11 ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A11);
*ierr = MatSchurComplementGetSubMatrices(
	(Mat)PetscToPointer((S) ),A00,Ap00,A01,A10,A11);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A00_null && !*(void**) A00) * (void **) A00 = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! Ap00_null && !*(void**) Ap00) * (void **) Ap00 = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A01_null && !*(void**) A01) * (void **) A01 = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A10_null && !*(void**) A10) * (void **) A10 = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A11_null && !*(void**) A11) * (void **) A11 = (void *)-2;
}
PETSC_EXTERN void  matschurcomplementcomputeexplicitoperator_(Mat A,Mat *S, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool S_null = !*(void**) S ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(S);
*ierr = MatSchurComplementComputeExplicitOperator(
	(Mat)PetscToPointer((A) ),S);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! S_null && !*(void**) S) * (void **) S = (void *)-2;
}
PETSC_EXTERN void  matgetschurcomplement_(Mat A,IS isrow0,IS iscol0,IS isrow1,IS iscol1,MatReuse *mreuse,Mat *S,MatSchurComplementAinvType *ainvtype,MatReuse *preuse,Mat *Sp, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(isrow0);
CHKFORTRANNULLOBJECT(iscol0);
CHKFORTRANNULLOBJECT(isrow1);
CHKFORTRANNULLOBJECT(iscol1);
PetscBool S_null = !*(void**) S ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(S);
PetscBool Sp_null = !*(void**) Sp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(Sp);
*ierr = MatGetSchurComplement(
	(Mat)PetscToPointer((A) ),
	(IS)PetscToPointer((isrow0) ),
	(IS)PetscToPointer((iscol0) ),
	(IS)PetscToPointer((isrow1) ),
	(IS)PetscToPointer((iscol1) ),*mreuse,S,*ainvtype,*preuse,Sp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! S_null && !*(void**) S) * (void **) S = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! Sp_null && !*(void**) Sp) * (void **) Sp = (void *)-2;
}
PETSC_EXTERN void  matschurcomplementsetainvtype_(Mat S,MatSchurComplementAinvType *ainvtype, int *ierr)
{
CHKFORTRANNULLOBJECT(S);
*ierr = MatSchurComplementSetAinvType(
	(Mat)PetscToPointer((S) ),*ainvtype);
}
PETSC_EXTERN void  matschurcomplementgetainvtype_(Mat S,MatSchurComplementAinvType *ainvtype, int *ierr)
{
CHKFORTRANNULLOBJECT(S);
*ierr = MatSchurComplementGetAinvType(
	(Mat)PetscToPointer((S) ),ainvtype);
}
PETSC_EXTERN void  matcreateschurcomplementpmat_(Mat A00,Mat A01,Mat A10,Mat A11,MatSchurComplementAinvType *ainvtype,MatReuse *preuse,Mat *Sp, int *ierr)
{
CHKFORTRANNULLOBJECT(A00);
CHKFORTRANNULLOBJECT(A01);
CHKFORTRANNULLOBJECT(A10);
CHKFORTRANNULLOBJECT(A11);
PetscBool Sp_null = !*(void**) Sp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(Sp);
*ierr = MatCreateSchurComplementPmat(
	(Mat)PetscToPointer((A00) ),
	(Mat)PetscToPointer((A01) ),
	(Mat)PetscToPointer((A10) ),
	(Mat)PetscToPointer((A11) ),*ainvtype,*preuse,Sp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! Sp_null && !*(void**) Sp) * (void **) Sp = (void *)-2;
}
PETSC_EXTERN void  matschurcomplementgetpmat_(Mat S,MatReuse *preuse,Mat *Sp, int *ierr)
{
CHKFORTRANNULLOBJECT(S);
PetscBool Sp_null = !*(void**) Sp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(Sp);
*ierr = MatSchurComplementGetPmat(
	(Mat)PetscToPointer((S) ),*preuse,Sp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! Sp_null && !*(void**) Sp) * (void **) Sp = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
