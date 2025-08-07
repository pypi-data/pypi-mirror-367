#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* fasfunc.c */
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

#include "petscsnes.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfassettype_ SNESFASSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfassettype_ snesfassettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfasgettype_ SNESFASGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfasgettype_ snesfasgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfasgetlevels_ SNESFASGETLEVELS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfasgetlevels_ snesfasgetlevels
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfasgetcyclesnes_ SNESFASGETCYCLESNES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfasgetcyclesnes_ snesfasgetcyclesnes
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfassetnumbersmoothup_ SNESFASSETNUMBERSMOOTHUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfassetnumbersmoothup_ snesfassetnumbersmoothup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfassetnumbersmoothdown_ SNESFASSETNUMBERSMOOTHDOWN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfassetnumbersmoothdown_ snesfassetnumbersmoothdown
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfassetcontinuation_ SNESFASSETCONTINUATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfassetcontinuation_ snesfassetcontinuation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfassetcycles_ SNESFASSETCYCLES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfassetcycles_ snesfassetcycles
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfassetlog_ SNESFASSETLOG
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfassetlog_ snesfassetlog
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfascyclesetcycles_ SNESFASCYCLESETCYCLES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfascyclesetcycles_ snesfascyclesetcycles
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfascyclegetsmoother_ SNESFASCYCLEGETSMOOTHER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfascyclegetsmoother_ snesfascyclegetsmoother
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfascyclegetsmootherup_ SNESFASCYCLEGETSMOOTHERUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfascyclegetsmootherup_ snesfascyclegetsmootherup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfascyclegetsmootherdown_ SNESFASCYCLEGETSMOOTHERDOWN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfascyclegetsmootherdown_ snesfascyclegetsmootherdown
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfascyclegetcorrection_ SNESFASCYCLEGETCORRECTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfascyclegetcorrection_ snesfascyclegetcorrection
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfascyclegetinterpolation_ SNESFASCYCLEGETINTERPOLATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfascyclegetinterpolation_ snesfascyclegetinterpolation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfascyclegetrestriction_ SNESFASCYCLEGETRESTRICTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfascyclegetrestriction_ snesfascyclegetrestriction
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfascyclegetinjection_ SNESFASCYCLEGETINJECTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfascyclegetinjection_ snesfascyclegetinjection
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfascyclegetrscale_ SNESFASCYCLEGETRSCALE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfascyclegetrscale_ snesfascyclegetrscale
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfascycleisfine_ SNESFASCYCLEISFINE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfascycleisfine_ snesfascycleisfine
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfassetinterpolation_ SNESFASSETINTERPOLATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfassetinterpolation_ snesfassetinterpolation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfasgetinterpolation_ SNESFASGETINTERPOLATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfasgetinterpolation_ snesfasgetinterpolation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfassetrestriction_ SNESFASSETRESTRICTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfassetrestriction_ snesfassetrestriction
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfasgetrestriction_ SNESFASGETRESTRICTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfasgetrestriction_ snesfasgetrestriction
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfassetinjection_ SNESFASSETINJECTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfassetinjection_ snesfassetinjection
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfasgetinjection_ SNESFASGETINJECTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfasgetinjection_ snesfasgetinjection
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfassetrscale_ SNESFASSETRSCALE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfassetrscale_ snesfassetrscale
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfasgetsmoother_ SNESFASGETSMOOTHER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfasgetsmoother_ snesfasgetsmoother
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfasgetsmootherdown_ SNESFASGETSMOOTHERDOWN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfasgetsmootherdown_ snesfasgetsmootherdown
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfasgetsmootherup_ SNESFASGETSMOOTHERUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfasgetsmootherup_ snesfasgetsmootherup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfasgetcoarsesolve_ SNESFASGETCOARSESOLVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfasgetcoarsesolve_ snesfasgetcoarsesolve
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfasfullsetdownsweep_ SNESFASFULLSETDOWNSWEEP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfasfullsetdownsweep_ snesfasfullsetdownsweep
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfasfullsettotal_ SNESFASFULLSETTOTAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfasfullsettotal_ snesfasfullsettotal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfasfullgettotal_ SNESFASFULLGETTOTAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfasfullgettotal_ snesfasfullgettotal
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  snesfassettype_(SNES snes,SNESFASType *fastype, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESFASSetType(
	(SNES)PetscToPointer((snes) ),*fastype);
}
PETSC_EXTERN void  snesfasgettype_(SNES snes,SNESFASType *fastype, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESFASGetType(
	(SNES)PetscToPointer((snes) ),fastype);
}
PETSC_EXTERN void  snesfasgetlevels_(SNES snes,PetscInt *levels, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLINTEGER(levels);
*ierr = SNESFASGetLevels(
	(SNES)PetscToPointer((snes) ),levels);
}
PETSC_EXTERN void  snesfasgetcyclesnes_(SNES snes,PetscInt *level,SNES *lsnes, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool lsnes_null = !*(void**) lsnes ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(lsnes);
*ierr = SNESFASGetCycleSNES(
	(SNES)PetscToPointer((snes) ),*level,lsnes);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! lsnes_null && !*(void**) lsnes) * (void **) lsnes = (void *)-2;
}
PETSC_EXTERN void  snesfassetnumbersmoothup_(SNES snes,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESFASSetNumberSmoothUp(
	(SNES)PetscToPointer((snes) ),*n);
}
PETSC_EXTERN void  snesfassetnumbersmoothdown_(SNES snes,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESFASSetNumberSmoothDown(
	(SNES)PetscToPointer((snes) ),*n);
}
PETSC_EXTERN void  snesfassetcontinuation_(SNES snes,PetscBool *continuation, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESFASSetContinuation(
	(SNES)PetscToPointer((snes) ),*continuation);
}
PETSC_EXTERN void  snesfassetcycles_(SNES snes,PetscInt *cycles, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESFASSetCycles(
	(SNES)PetscToPointer((snes) ),*cycles);
}
PETSC_EXTERN void  snesfassetlog_(SNES snes,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESFASSetLog(
	(SNES)PetscToPointer((snes) ),*flg);
}
PETSC_EXTERN void  snesfascyclesetcycles_(SNES snes,PetscInt *cycles, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESFASCycleSetCycles(
	(SNES)PetscToPointer((snes) ),*cycles);
}
PETSC_EXTERN void  snesfascyclegetsmoother_(SNES snes,SNES *smooth, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool smooth_null = !*(void**) smooth ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(smooth);
*ierr = SNESFASCycleGetSmoother(
	(SNES)PetscToPointer((snes) ),smooth);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! smooth_null && !*(void**) smooth) * (void **) smooth = (void *)-2;
}
PETSC_EXTERN void  snesfascyclegetsmootherup_(SNES snes,SNES *smoothu, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool smoothu_null = !*(void**) smoothu ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(smoothu);
*ierr = SNESFASCycleGetSmootherUp(
	(SNES)PetscToPointer((snes) ),smoothu);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! smoothu_null && !*(void**) smoothu) * (void **) smoothu = (void *)-2;
}
PETSC_EXTERN void  snesfascyclegetsmootherdown_(SNES snes,SNES *smoothd, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool smoothd_null = !*(void**) smoothd ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(smoothd);
*ierr = SNESFASCycleGetSmootherDown(
	(SNES)PetscToPointer((snes) ),smoothd);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! smoothd_null && !*(void**) smoothd) * (void **) smoothd = (void *)-2;
}
PETSC_EXTERN void  snesfascyclegetcorrection_(SNES snes,SNES *correction, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool correction_null = !*(void**) correction ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(correction);
*ierr = SNESFASCycleGetCorrection(
	(SNES)PetscToPointer((snes) ),correction);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! correction_null && !*(void**) correction) * (void **) correction = (void *)-2;
}
PETSC_EXTERN void  snesfascyclegetinterpolation_(SNES snes,Mat *mat, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
*ierr = SNESFASCycleGetInterpolation(
	(SNES)PetscToPointer((snes) ),mat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
PETSC_EXTERN void  snesfascyclegetrestriction_(SNES snes,Mat *mat, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
*ierr = SNESFASCycleGetRestriction(
	(SNES)PetscToPointer((snes) ),mat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
PETSC_EXTERN void  snesfascyclegetinjection_(SNES snes,Mat *mat, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
*ierr = SNESFASCycleGetInjection(
	(SNES)PetscToPointer((snes) ),mat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
PETSC_EXTERN void  snesfascyclegetrscale_(SNES snes,Vec *vec, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool vec_null = !*(void**) vec ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vec);
*ierr = SNESFASCycleGetRScale(
	(SNES)PetscToPointer((snes) ),vec);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vec_null && !*(void**) vec) * (void **) vec = (void *)-2;
}
PETSC_EXTERN void  snesfascycleisfine_(SNES snes,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESFASCycleIsFine(
	(SNES)PetscToPointer((snes) ),flg);
}
PETSC_EXTERN void  snesfassetinterpolation_(SNES snes,PetscInt *level,Mat mat, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(mat);
*ierr = SNESFASSetInterpolation(
	(SNES)PetscToPointer((snes) ),*level,
	(Mat)PetscToPointer((mat) ));
}
PETSC_EXTERN void  snesfasgetinterpolation_(SNES snes,PetscInt *level,Mat *mat, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
*ierr = SNESFASGetInterpolation(
	(SNES)PetscToPointer((snes) ),*level,mat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
PETSC_EXTERN void  snesfassetrestriction_(SNES snes,PetscInt *level,Mat mat, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(mat);
*ierr = SNESFASSetRestriction(
	(SNES)PetscToPointer((snes) ),*level,
	(Mat)PetscToPointer((mat) ));
}
PETSC_EXTERN void  snesfasgetrestriction_(SNES snes,PetscInt *level,Mat *mat, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
*ierr = SNESFASGetRestriction(
	(SNES)PetscToPointer((snes) ),*level,mat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
PETSC_EXTERN void  snesfassetinjection_(SNES snes,PetscInt *level,Mat mat, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(mat);
*ierr = SNESFASSetInjection(
	(SNES)PetscToPointer((snes) ),*level,
	(Mat)PetscToPointer((mat) ));
}
PETSC_EXTERN void  snesfasgetinjection_(SNES snes,PetscInt *level,Mat *mat, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
*ierr = SNESFASGetInjection(
	(SNES)PetscToPointer((snes) ),*level,mat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
PETSC_EXTERN void  snesfassetrscale_(SNES snes,PetscInt *level,Vec rscale, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(rscale);
*ierr = SNESFASSetRScale(
	(SNES)PetscToPointer((snes) ),*level,
	(Vec)PetscToPointer((rscale) ));
}
PETSC_EXTERN void  snesfasgetsmoother_(SNES snes,PetscInt *level,SNES *smooth, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool smooth_null = !*(void**) smooth ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(smooth);
*ierr = SNESFASGetSmoother(
	(SNES)PetscToPointer((snes) ),*level,smooth);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! smooth_null && !*(void**) smooth) * (void **) smooth = (void *)-2;
}
PETSC_EXTERN void  snesfasgetsmootherdown_(SNES snes,PetscInt *level,SNES *smooth, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool smooth_null = !*(void**) smooth ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(smooth);
*ierr = SNESFASGetSmootherDown(
	(SNES)PetscToPointer((snes) ),*level,smooth);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! smooth_null && !*(void**) smooth) * (void **) smooth = (void *)-2;
}
PETSC_EXTERN void  snesfasgetsmootherup_(SNES snes,PetscInt *level,SNES *smooth, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool smooth_null = !*(void**) smooth ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(smooth);
*ierr = SNESFASGetSmootherUp(
	(SNES)PetscToPointer((snes) ),*level,smooth);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! smooth_null && !*(void**) smooth) * (void **) smooth = (void *)-2;
}
PETSC_EXTERN void  snesfasgetcoarsesolve_(SNES snes,SNES *coarse, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool coarse_null = !*(void**) coarse ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(coarse);
*ierr = SNESFASGetCoarseSolve(
	(SNES)PetscToPointer((snes) ),coarse);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! coarse_null && !*(void**) coarse) * (void **) coarse = (void *)-2;
}
PETSC_EXTERN void  snesfasfullsetdownsweep_(SNES snes,PetscBool *swp, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESFASFullSetDownSweep(
	(SNES)PetscToPointer((snes) ),*swp);
}
PETSC_EXTERN void  snesfasfullsettotal_(SNES snes,PetscBool *total, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESFASFullSetTotal(
	(SNES)PetscToPointer((snes) ),*total);
}
PETSC_EXTERN void  snesfasfullgettotal_(SNES snes,PetscBool *total, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESFASFullGetTotal(
	(SNES)PetscToPointer((snes) ),total);
}
#if defined(__cplusplus)
}
#endif
