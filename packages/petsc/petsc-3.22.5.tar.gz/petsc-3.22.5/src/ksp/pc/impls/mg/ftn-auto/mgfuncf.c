#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* mgfunc.c */
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
#define pcmgresidualdefault_ PCMGRESIDUALDEFAULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmgresidualdefault_ pcmgresidualdefault
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmgresidualtransposedefault_ PCMGRESIDUALTRANSPOSEDEFAULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmgresidualtransposedefault_ pcmgresidualtransposedefault
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmgmatresidualdefault_ PCMGMATRESIDUALDEFAULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmgmatresidualdefault_ pcmgmatresidualdefault
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmgmatresidualtransposedefault_ PCMGMATRESIDUALTRANSPOSEDEFAULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmgmatresidualtransposedefault_ pcmgmatresidualtransposedefault
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmggetcoarsesolve_ PCMGGETCOARSESOLVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmggetcoarsesolve_ pcmggetcoarsesolve
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmgsetinterpolation_ PCMGSETINTERPOLATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmgsetinterpolation_ pcmgsetinterpolation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmgsetoperators_ PCMGSETOPERATORS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmgsetoperators_ pcmgsetoperators
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmggetinterpolation_ PCMGGETINTERPOLATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmggetinterpolation_ pcmggetinterpolation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmgsetrestriction_ PCMGSETRESTRICTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmgsetrestriction_ pcmgsetrestriction
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmggetrestriction_ PCMGGETRESTRICTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmggetrestriction_ pcmggetrestriction
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmgsetrscale_ PCMGSETRSCALE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmgsetrscale_ pcmgsetrscale
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmggetrscale_ PCMGGETRSCALE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmggetrscale_ pcmggetrscale
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmgsetinjection_ PCMGSETINJECTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmgsetinjection_ pcmgsetinjection
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmggetinjection_ PCMGGETINJECTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmggetinjection_ pcmggetinjection
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmggetsmoother_ PCMGGETSMOOTHER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmggetsmoother_ pcmggetsmoother
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmggetsmootherup_ PCMGGETSMOOTHERUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmggetsmootherup_ pcmggetsmootherup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmggetsmootherdown_ PCMGGETSMOOTHERDOWN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmggetsmootherdown_ pcmggetsmootherdown
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmgsetcycletypeonlevel_ PCMGSETCYCLETYPEONLEVEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmgsetcycletypeonlevel_ pcmgsetcycletypeonlevel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmgsetrhs_ PCMGSETRHS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmgsetrhs_ pcmgsetrhs
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmgsetx_ PCMGSETX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmgsetx_ pcmgsetx
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmgsetr_ PCMGSETR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmgsetr_ pcmgsetr
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  pcmgresidualdefault_(Mat mat,Vec b,Vec x,Vec r, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(b);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(r);
*ierr = PCMGResidualDefault(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((b) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((r) ));
}
PETSC_EXTERN void  pcmgresidualtransposedefault_(Mat mat,Vec b,Vec x,Vec r, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(b);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(r);
*ierr = PCMGResidualTransposeDefault(
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((b) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((r) ));
}
PETSC_EXTERN void  pcmgmatresidualdefault_(Mat mat,Mat b,Mat x,Mat r, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(b);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(r);
*ierr = PCMGMatResidualDefault(
	(Mat)PetscToPointer((mat) ),
	(Mat)PetscToPointer((b) ),
	(Mat)PetscToPointer((x) ),
	(Mat)PetscToPointer((r) ));
}
PETSC_EXTERN void  pcmgmatresidualtransposedefault_(Mat mat,Mat b,Mat x,Mat r, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(b);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(r);
*ierr = PCMGMatResidualTransposeDefault(
	(Mat)PetscToPointer((mat) ),
	(Mat)PetscToPointer((b) ),
	(Mat)PetscToPointer((x) ),
	(Mat)PetscToPointer((r) ));
}
PETSC_EXTERN void  pcmggetcoarsesolve_(PC pc,KSP *ksp, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool ksp_null = !*(void**) ksp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ksp);
*ierr = PCMGGetCoarseSolve(
	(PC)PetscToPointer((pc) ),ksp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ksp_null && !*(void**) ksp) * (void **) ksp = (void *)-2;
}
PETSC_EXTERN void  pcmgsetinterpolation_(PC pc,PetscInt *l,Mat mat, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(mat);
*ierr = PCMGSetInterpolation(
	(PC)PetscToPointer((pc) ),*l,
	(Mat)PetscToPointer((mat) ));
}
PETSC_EXTERN void  pcmgsetoperators_(PC pc,PetscInt *l,Mat Amat,Mat Pmat, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(Amat);
CHKFORTRANNULLOBJECT(Pmat);
*ierr = PCMGSetOperators(
	(PC)PetscToPointer((pc) ),*l,
	(Mat)PetscToPointer((Amat) ),
	(Mat)PetscToPointer((Pmat) ));
}
PETSC_EXTERN void  pcmggetinterpolation_(PC pc,PetscInt *l,Mat *mat, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
*ierr = PCMGGetInterpolation(
	(PC)PetscToPointer((pc) ),*l,mat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
PETSC_EXTERN void  pcmgsetrestriction_(PC pc,PetscInt *l,Mat mat, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(mat);
*ierr = PCMGSetRestriction(
	(PC)PetscToPointer((pc) ),*l,
	(Mat)PetscToPointer((mat) ));
}
PETSC_EXTERN void  pcmggetrestriction_(PC pc,PetscInt *l,Mat *mat, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
*ierr = PCMGGetRestriction(
	(PC)PetscToPointer((pc) ),*l,mat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
PETSC_EXTERN void  pcmgsetrscale_(PC pc,PetscInt *l,Vec rscale, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(rscale);
*ierr = PCMGSetRScale(
	(PC)PetscToPointer((pc) ),*l,
	(Vec)PetscToPointer((rscale) ));
}
PETSC_EXTERN void  pcmggetrscale_(PC pc,PetscInt *l,Vec *rscale, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool rscale_null = !*(void**) rscale ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(rscale);
*ierr = PCMGGetRScale(
	(PC)PetscToPointer((pc) ),*l,rscale);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! rscale_null && !*(void**) rscale) * (void **) rscale = (void *)-2;
}
PETSC_EXTERN void  pcmgsetinjection_(PC pc,PetscInt *l,Mat mat, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(mat);
*ierr = PCMGSetInjection(
	(PC)PetscToPointer((pc) ),*l,
	(Mat)PetscToPointer((mat) ));
}
PETSC_EXTERN void  pcmggetinjection_(PC pc,PetscInt *l,Mat *mat, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
*ierr = PCMGGetInjection(
	(PC)PetscToPointer((pc) ),*l,mat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
PETSC_EXTERN void  pcmggetsmoother_(PC pc,PetscInt *l,KSP *ksp, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool ksp_null = !*(void**) ksp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ksp);
*ierr = PCMGGetSmoother(
	(PC)PetscToPointer((pc) ),*l,ksp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ksp_null && !*(void**) ksp) * (void **) ksp = (void *)-2;
}
PETSC_EXTERN void  pcmggetsmootherup_(PC pc,PetscInt *l,KSP *ksp, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool ksp_null = !*(void**) ksp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ksp);
*ierr = PCMGGetSmootherUp(
	(PC)PetscToPointer((pc) ),*l,ksp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ksp_null && !*(void**) ksp) * (void **) ksp = (void *)-2;
}
PETSC_EXTERN void  pcmggetsmootherdown_(PC pc,PetscInt *l,KSP *ksp, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool ksp_null = !*(void**) ksp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ksp);
*ierr = PCMGGetSmootherDown(
	(PC)PetscToPointer((pc) ),*l,ksp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ksp_null && !*(void**) ksp) * (void **) ksp = (void *)-2;
}
PETSC_EXTERN void  pcmgsetcycletypeonlevel_(PC pc,PetscInt *l,PCMGCycleType *c, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCMGSetCycleTypeOnLevel(
	(PC)PetscToPointer((pc) ),*l,*c);
}
PETSC_EXTERN void  pcmgsetrhs_(PC pc,PetscInt *l,Vec c, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(c);
*ierr = PCMGSetRhs(
	(PC)PetscToPointer((pc) ),*l,
	(Vec)PetscToPointer((c) ));
}
PETSC_EXTERN void  pcmgsetx_(PC pc,PetscInt *l,Vec c, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(c);
*ierr = PCMGSetX(
	(PC)PetscToPointer((pc) ),*l,
	(Vec)PetscToPointer((c) ));
}
PETSC_EXTERN void  pcmgsetr_(PC pc,PetscInt *l,Vec c, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(c);
*ierr = PCMGSetR(
	(PC)PetscToPointer((pc) ),*l,
	(Vec)PetscToPointer((c) ));
}
#if defined(__cplusplus)
}
#endif
